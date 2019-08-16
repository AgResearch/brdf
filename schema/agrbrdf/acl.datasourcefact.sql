--
-- Name: datasourcefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourcefact FROM PUBLIC;
REVOKE ALL ON TABLE datasourcefact FROM agrbrdf;
GRANT ALL ON TABLE datasourcefact TO agrbrdf;
GRANT SELECT ON TABLE datasourcefact TO gbs;


