--
-- Name: microarrayobservationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayobservationfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayobservationfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayobservationfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayobservationfact TO gbs;


