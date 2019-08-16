--
-- Name: genotypes; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE genotypes FROM PUBLIC;
REVOKE ALL ON TABLE genotypes FROM agrbrdf;
GRANT ALL ON TABLE genotypes TO agrbrdf;
GRANT SELECT ON TABLE genotypes TO gbs;


