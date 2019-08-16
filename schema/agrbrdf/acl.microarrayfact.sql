--
-- Name: microarrayfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayfact FROM PUBLIC;
REVOKE ALL ON TABLE microarrayfact FROM agrbrdf;
GRANT ALL ON TABLE microarrayfact TO agrbrdf;
GRANT SELECT ON TABLE microarrayfact TO gbs;


