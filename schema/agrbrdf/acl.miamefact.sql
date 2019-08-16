--
-- Name: miamefact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE miamefact FROM PUBLIC;
REVOKE ALL ON TABLE miamefact FROM agrbrdf;
GRANT ALL ON TABLE miamefact TO agrbrdf;
GRANT SELECT ON TABLE miamefact TO gbs;


