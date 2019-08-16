--
-- Name: accessfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE accessfact FROM PUBLIC;
REVOKE ALL ON TABLE accessfact FROM agrbrdf;
GRANT ALL ON TABLE accessfact TO agrbrdf;
GRANT SELECT ON TABLE accessfact TO gbs;


