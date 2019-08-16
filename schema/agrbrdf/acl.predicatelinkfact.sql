--
-- Name: predicatelinkfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE predicatelinkfact FROM PUBLIC;
REVOKE ALL ON TABLE predicatelinkfact FROM agrbrdf;
GRANT ALL ON TABLE predicatelinkfact TO agrbrdf;
GRANT SELECT ON TABLE predicatelinkfact TO gbs;


